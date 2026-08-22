import { useState } from 'react';
import { Share2, Copy, Check, Trash2 } from 'lucide-react';
import { Modal } from '../../components/ui/Modal';
import { Button } from '../../components/ui/Button';
import { publishTrip, unpublishTrip } from './sharingApi';

export const ShareTripModal = ({ isOpen, onClose, tripId }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [shareData, setShareData] = useState(null);
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState("");

  const handlePublish = async () => {
    setIsLoading(true);
    setError("");
    try {
      const data = await publishTrip(tripId);
      setShareData(data);
    } catch (err) {
      setError("Failed to generate share link.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleUnpublish = async () => {
    setIsLoading(true);
    try {
      await unpublishTrip(tripId);
      setShareData(null);
    } catch (err) {
      setError("Failed to revoke link.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopyLink = () => {
    if (!shareData) return;
    const fullUrl = `${window.location.origin}/shared/${shareData.slug}`;
    navigator.clipboard.writeText(fullUrl);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Share Trip Itinerary">
      <div className="space-y-4">
        <p className="text-sm text-text-secondary">
          Publish this trip to generate a public, read-only link. Anyone with the link will be able to view your itinerary and copy it to their own account.
        </p>

        {error && <div className="text-sm text-error bg-error-soft p-3 rounded-xl">{error}</div>}

        {!shareData ? (
          <Button onClick={handlePublish} isLoading={isLoading} className="w-full gap-2">
            <Share2 size={18} /> Generate Public Link
          </Button>
        ) : (
          <div className="space-y-4">
            <div className="flex items-center gap-2 p-3 bg-surface-muted border border-border-default rounded-xl">
              <span className="text-sm text-text-primary truncate flex-1 select-all">
                {`${window.location.origin}/shared/${shareData.slug}`}
              </span>
              <Button variant="secondary" size="sm" onClick={handleCopyLink} className="shrink-0 gap-2">
                {copied ? <Check size={16} className="text-success" /> : <Copy size={16} />}
                {copied ? "Copied!" : "Copy"}
              </Button>
            </div>
            
            <Button variant="ghost" onClick={handleUnpublish} isLoading={isLoading} className="w-full text-error hover:bg-error-soft gap-2">
              <Trash2 size={18} /> Revoke Link & Make Private
            </Button>
          </div>
        )}
      </div>
    </Modal>
  );
};